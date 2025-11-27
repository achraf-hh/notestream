package com.notestream.notestream_api.api;

import com.notestream.notestream_api.domain.model.Course;
import com.notestream.notestream_api.domain.repository.CourseRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/courses")
public class CourseController {

    private final CourseRepository courseRepository;

    public CourseController(CourseRepository courseRepository) {
        this.courseRepository = courseRepository;
    }

    @PostMapping
    public ResponseEntity<Course> createCourse(@RequestBody Map<String, String> body) {
        String name = body.get("name");
        String description = body.get("description");
        
        Course course = new Course(name, description);
        course = courseRepository.save(course);
        
        return ResponseEntity.status(HttpStatus.CREATED).body(course);
    }

    @GetMapping
    public ResponseEntity<List<Course>> getAllCourses() {
        return ResponseEntity.ok(courseRepository.findAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Course> getCourse(@PathVariable Long id) {
        return courseRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @DeleteMapping("/{id}")
public ResponseEntity<Void> deleteCourse(@PathVariable Long id) {
    if (courseRepository.existsById(id)) {
        courseRepository.deleteById(id);
        return ResponseEntity.noContent().build(); 
    }
    return ResponseEntity.notFound().build(); 
}
}